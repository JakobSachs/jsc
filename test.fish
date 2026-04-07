#!/usr/bin/env fish
#
# Simple test harness for the jsc compiler (Python module).
# Mirrors the logic in tests/test_compiler.sh but written in fish.
#
# Usage:
#   ./test.fish [stages...]
#   ./test.fish          # run all stages (1-10)
#   ./test.fish 1 2 4    # run specific stages

set padlength 50
set success_total 0
set failure_total 0

function pad_name
    set -l name $argv[1]
    set -l dots (string repeat -n (math $padlength - (string length $name)) .)
    printf '%s%s' $name $dots
end

function run_correct_program
    set -g expected_out (./a.out 2>/dev/null)
    set -g expected_exit $status
    rm -f a.out
end

function run_our_program
    if test -f $argv[1]
        set -g actual_out (./$argv[1] 2>/dev/null)
        set -g actual_exit $status
        rm -f $argv[1]
    else
        set -g actual_out ""
        set -g actual_exit 255
    end
end

function test_stage
    set -l stage $argv[1]
    set -l success 0
    set -l fail 0

    echo "===================================================="
    echo "STAGE $stage"
    echo "===================Valid Programs==================="

    for prog in (find tests/stage_$stage/valid -type f -name "*.c" ! -path "*/valid_multifile/*" 2>/dev/null)
        # compile with gcc to get expected result
        gcc -w $prog
        run_correct_program

        # derive base name and test name
        set -l base (string replace -r '\.c$' '' $prog)
        set -l test_name (string replace -r '.*valid/' '' $base)

        pad_name $test_name

        # compile with jsc
        uv run python -m jsc $prog 2>/dev/null
        set -l comp_status $status

        if string match -q 'skip_on_failure*' $test_name
            if test -f $base; and test $comp_status -eq 0
                run_our_program $base
                if test "$expected_exit" -eq "$actual_exit"; and test "$expected_out" = "$actual_out"
                    echo "OK"
                    set success (math $success + 1)
                else
                    echo "FAIL"
                    set fail (math $fail + 1)
                end
            else
                echo "NOT IMPLEMENTED"
            end
        else
            run_our_program $base
            if test "$expected_exit" -eq "$actual_exit"; and test "$expected_out" = "$actual_out"
                echo "OK"
                set success (math $success + 1)
            else
                echo "FAIL"
                set fail (math $fail + 1)
            end
        end
    end

    # multifile programs
    for dir in (find tests/stage_$stage/valid_multifile -mindepth 1 -maxdepth 1 -type d 2>/dev/null)
        gcc -w $dir/*
        run_correct_program

        set -l test_name (basename $dir)
        uv run python -m jsc -o $test_name $dir/* >/dev/null 2>&1

        pad_name $test_name
        run_our_program $test_name
        if test "$expected_exit" -eq "$actual_exit"; and test "$expected_out" = "$actual_out"
            echo "OK"
            set success (math $success + 1)
        else
            echo "FAIL"
            set fail (math $fail + 1)
        end
    end

    echo "===================Invalid Programs================="

    for prog in (find tests/stage_$stage/invalid -type f -name "*.c" 2>/dev/null)
        set -l base (string replace -r '\.c$' '' $prog)
        set -l test_name (string replace -r '.*invalid/' '' $base)

        uv run python -m jsc $prog >/dev/null 2>&1
        set -l comp_status $status

        pad_name $test_name

        if test -f $base; or test -f "$base.s"
            echo "FAIL"
            set fail (math $fail + 1)
            rm -f $base "$base.s"
        else if test $comp_status -ne 0
            echo "OK"
            set success (math $success + 1)
        else
            echo "FAIL"
            set fail (math $fail + 1)
        end
    end

    echo "===================Stage $stage Summary================="
    printf "%d successes, %d failures\n" $success $fail
    set success_total (math $success_total + $success)
    set failure_total (math $failure_total + $fail)
end

function total_summary
    echo "===================TOTAL SUMMARY===================="
    printf "%d successes, %d failures\n" $success_total $failure_total
end

# --- main ---

if test (count $argv) -gt 0
    for stage in $argv
        test_stage $stage
    end
else
    for stage in (seq 1 10)
        test_stage $stage
    end
end

total_summary
