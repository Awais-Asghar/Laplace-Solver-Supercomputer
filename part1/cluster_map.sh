#!/bin/bash
# ============================================================
# Part I: HPC Cluster Mapper
# Maps all compute nodes, CPU specs, availability, and ranks
# Run this on the HPC head node (afrit)
# ============================================================

OUTPUT_FILE="cluster_report.txt"
CSV_FILE="cluster_data.csv"

echo "=============================================" | tee $OUTPUT_FILE
echo "   HPC CLUSTER MAP - $(date)"                 | tee -a $OUTPUT_FILE
echo "=============================================" | tee -a $OUTPUT_FILE
echo ""                                             | tee -a $OUTPUT_FILE

# CSV header
echo "Node,Status,CPUs,Cores_Per_CPU,Total_Cores,RAM_GB,Load_1min,Load_5min,Load_15min,CPU_Usage_Percent,Free_RAM_GB,Score" > $CSV_FILE

echo "[1] HEAD NODE INFO" | tee -a $OUTPUT_FILE
echo "-------------------------------------------" | tee -a $OUTPUT_FILE
hostname | tee -a $OUTPUT_FILE
lscpu | grep -E "Socket|Core|Thread|Model name|CPU\(s\)" | tee -a $OUTPUT_FILE
free -h | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

echo "[2] SCANNING COMPUTE NODES (compute-0-0 to compute-0-28)" | tee -a $OUTPUT_FILE
echo "-------------------------------------------" | tee -a $OUTPUT_FILE

declare -A node_scores

for i in $(seq 0 28); do
    NODE="compute-0-$i"
    echo -n "Checking $NODE ... " | tee -a $OUTPUT_FILE

    # Check if node is reachable
    if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "echo ok" &>/dev/null; then
        echo "ONLINE" | tee -a $OUTPUT_FILE

        # Gather CPU info
        CPU_MODEL=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "lscpu | grep 'Model name' | awk -F: '{print \$2}' | xargs")
        SOCKETS=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "lscpu | grep '^Socket(s)' | awk '{print \$2}'")
        CORES_PER_SOCKET=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "lscpu | grep 'Core(s) per socket' | awk '{print \$4}'")
        THREADS=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "lscpu | grep '^Thread(s) per core' | awk '{print \$4}'")
        TOTAL_CPUS=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "nproc")
        TOTAL_CORES=$((SOCKETS * CORES_PER_SOCKET))

        # RAM info
        TOTAL_RAM=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "free -g | awk '/Mem/{print \$2}'")
        FREE_RAM=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "free -g | awk '/Mem/{print \$7}'")

        # Load average (1min, 5min, 15min)
        LOAD=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "cat /proc/loadavg | awk '{print \$1, \$2, \$3}'")
        LOAD_1=$(echo $LOAD | awk '{print $1}')
        LOAD_5=$(echo $LOAD | awk '{print $2}')
        LOAD_15=$(echo $LOAD | awk '{print $3}')

        # CPU usage %
        CPU_USAGE=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | tr -d '%us,'")

        # Running processes count (non-idle)
        PROCS=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $NODE "ps aux | grep -v root | grep -v '^USER' | wc -l")

        # Availability score: higher is better
        # Score = (Free RAM / Total RAM) * 50 + (1 - CPU_Usage/100) * 50
        FREE_RAM_PCT=$(echo "scale=2; $FREE_RAM / ($TOTAL_RAM + 0.001) * 100" | bc 2>/dev/null || echo "50")
        CPU_IDLE=$(echo "scale=2; 100 - $CPU_USAGE" | bc 2>/dev/null || echo "50")
        SCORE=$(echo "scale=0; ($FREE_RAM_PCT + $CPU_IDLE) / 2" | bc 2>/dev/null || echo "50")

        node_scores[$NODE]=$SCORE

        # Print details
        echo "   CPU Model   : $CPU_MODEL"         | tee -a $OUTPUT_FILE
        echo "   Sockets     : $SOCKETS"            | tee -a $OUTPUT_FILE
        echo "   Cores/Socket: $CORES_PER_SOCKET"   | tee -a $OUTPUT_FILE
        echo "   Threads/Core: $THREADS"            | tee -a $OUTPUT_FILE
        echo "   Total CPUs  : $TOTAL_CPUS"         | tee -a $OUTPUT_FILE
        echo "   RAM Total   : ${TOTAL_RAM} GB"     | tee -a $OUTPUT_FILE
        echo "   RAM Free    : ${FREE_RAM} GB"      | tee -a $OUTPUT_FILE
        echo "   Load (1/5/15): $LOAD_1 / $LOAD_5 / $LOAD_15" | tee -a $OUTPUT_FILE
        echo "   CPU Usage   : ${CPU_USAGE}%"       | tee -a $OUTPUT_FILE
        echo "   User Procs  : $PROCS"              | tee -a $OUTPUT_FILE
        echo "   Avail Score : $SCORE / 100"        | tee -a $OUTPUT_FILE

        # Write CSV
        echo "$NODE,ONLINE,$TOTAL_CPUS,$CORES_PER_SOCKET,$TOTAL_CORES,$TOTAL_RAM,$LOAD_1,$LOAD_5,$LOAD_15,$CPU_USAGE,$FREE_RAM,$SCORE" >> $CSV_FILE

    else
        echo "OFFLINE/UNREACHABLE" | tee -a $OUTPUT_FILE
        echo "$NODE,OFFLINE,0,0,0,0,0,0,0,100,0,0" >> $CSV_FILE
    fi
    echo "" | tee -a $OUTPUT_FILE
done

echo "=============================================" | tee -a $OUTPUT_FILE
echo "   NODE RANKING (by availability score)"      | tee -a $OUTPUT_FILE
echo "   Higher score = more available"             | tee -a $OUTPUT_FILE
echo "=============================================" | tee -a $OUTPUT_FILE

# Sort CSV by score descending (skip header)
echo "Rank | Node | Score | CPU% | Free RAM (GB)" | tee -a $OUTPUT_FILE
tail -n +2 $CSV_FILE | sort -t',' -k12 -rn | awk -F',' 'BEGIN{r=1} {printf "%4d | %-15s | %5s | %5s%% | %s GB\n", r++, $1, $12, $10, $11}' | tee -a $OUTPUT_FILE

echo ""
echo "Report saved to: $OUTPUT_FILE"
echo "CSV data saved to: $CSV_FILE"
echo "Use cluster_visualize.py to generate graphs."
