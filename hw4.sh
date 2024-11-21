#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage:"
    echo "  For indexing: $0 index <input_directory> <output_directory>"
    echo "  For querying: $0 retrieve [-d directory] <query terms...>"
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Get the command (first argument)
command="$1"
shift  # Remove first argument

case "$command" in
    "index")
        # Check if both directories are provided for indexing
        if [ $# -ne 2 ]; then
            echo "Error: Indexing requires input and output directories"
            usage
        fi
        
        inputDirectory="$1"
        outputDirectory="$2"
        
        # Run the indexing program
        python3 hw4.py "$inputDirectory" "$outputDirectory"
        
        # Display file information
        echo -e "\nGenerated files:"
        ls -l "$outputDirectory"
        echo -e "\nFile sizes (line counts):"
        wc -l "$outputDirectory"/*
        ;;
        
    "retrieve")
        # Handle optional directory flag
        directory="."  # Default to current directory
        if [ "$1" = "-d" ]; then
            if [ $# -lt 3 ]; then
                echo "Error: -d requires a directory path and at least one query term"
                usage
            fi
            directory="$2"
            shift 2  # Remove -d and directory path
        fi
        
        # Check if there are query terms
        if [ $# -lt 1 ]; then
            echo "Error: No query terms provided"
            usage
        fi
        
        # Run the query processor with all remaining arguments as query terms
        python3 query_processor.py -d "$directory" "$@"
        ;;
        
    *)
        echo "Error: Unknown command '$command'"
        usage
        ;;
esac