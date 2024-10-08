#!/bin/bash

# Initialize counters
passed=0
failed=0
declare -A failed_files  # Associative array to store failed file names and messages

# Loop through all .yaml and .json files in the current directory
for file in *.yaml *.yml *.json; do
  # Check if the file exists to avoid errors
  if [[ -f "$file" ]]; then
    # Validate the CloudFormation template and capture the error message
    error_message=$(aws cloudformation validate-template --template-body file://"$file" 2>&1)
    if [[ $? -eq 0 ]]; then
      ((passed++))  # Increment passed counter
    else
      echo "❌ Validation failed for $file"
      failed_files["$file"]="$error_message"  # Store the error message
      ((failed++))  # Increment failed counter
    fi
  fi
done

# Summary of results
echo "---- Summary ----"
echo "Total files validated: $((passed + failed))"
echo "Tests passed: $passed"
echo "Tests failed: $failed"

# List of failed files and their messages
if [[ $failed -gt 0 ]]; then
  echo "Failed files and messages:"
  for f in "${!failed_files[@]}"; do
    echo "- $f: ${failed_files[$f]}"
  done
fi
