#!/bin/bash
# Test Progress Monitor
# Monitors all 4 running tests and reports progress

echo "=================================="
echo "TEST PROGRESS MONITOR"
echo "$(date)"
echo "=================================="

# Check result files
check_test() {
    local test_name=$1
    local result_file=$2

    if [ -f "$result_file" ]; then
        echo "✅ $test_name: COMPLETE"
        return 0
    else
        echo "🔄 $test_name: RUNNING"
        return 1
    fi
}

echo ""
echo "Test Status:"
echo "------------"

completed=0
check_test "Payload Complexity" "results_data/payload_complexity/payload_complexity_results.json" && ((completed++))
check_test "Seed Sensitivity  " "results_data/seed_sensitivity/seed_sensitivity_results.json" && ((completed++))
check_test "Reproducibility   " "results_data/reproducibility/reproducibility_results.json" && ((completed++))
check_test "Mutation Ablation " "results_data/mutation_ablation/mutation_ablation_results.json" && ((completed++))

echo ""
echo "Progress: $completed/4 tests completed"
echo "=================================="

if [ $completed -eq 4 ]; then
    echo "🎉 ALL TESTS COMPLETE!"
    echo ""
    echo "Next steps:"
    echo "1. python3 analysis_scripts/analyze_new_results.py"
    echo "2. python3 analysis_scripts/visualize_new_results.py"
    exit 0
else
    remaining=$((4 - completed))
    echo "⏳ $remaining tests still running..."
    exit 1
fi
