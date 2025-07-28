import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process tree counts and split data with a random seed and threshold.')
parser.add_argument('--seed_m', type=int, default=30, help='Random seed for splitting data (default: 30)')
parser.add_argument('--threshold', type=int, default=55, help='Threshold for number of trees per image (default: 55)')
args = parser.parse_args()

seed_m = args.seed_m
threshold = args.threshold

# Step 1: Compute histogram and statistics of tree counts in CSV files
csv_files = glob.glob('csv/image_*.csv')
counts = {}
for csv_file in csv_files:
    name = os.path.basename(csv_file).replace('.csv', '')
    with open(csv_file, 'r') as f:
        count = sum(1 for line in f) - 1  # Subtract 1 for header
    counts[name] = count

# Histogram
tree_counts = list(counts.values())
plt.figure(figsize=(10, 6))
plt.hist(tree_counts, bins=500, color='skyblue', edgecolor='black')
plt.title('Histogram of Number of Trees per Image')
plt.xlabel('Number of Trees')
plt.ylabel('Frequency')
plt.grid(True)
plt.savefig('tree_counts_histogram.png')
plt.close()

# Statistics
if tree_counts:
    mean_count = np.mean(tree_counts)
    median_count = np.median(tree_counts)
    min_count = np.min(tree_counts)
    max_count = np.max(tree_counts)
    print(f"Mean: {mean_count:.2f}, Median: {median_count}, Min: {min_count}, Max: {max_count}")
else:
    print("No CSV files found.")

# Step 2: Filter images with >= threshold trees
filtered_images = [name for name, count in counts.items() if count >= threshold]

# Split into 60% train, 20% val, 20% test
train, temp = train_test_split(filtered_images, test_size=0.2, random_state=seed_m)
val, test = train_test_split(temp, test_size=0.5, random_state=seed_m)

print(len(train))
print(len(test))
print(len(val))

# Write to files
with open('train.txt', 'w') as f:
    f.write('\n'.join(train) + '\n')
with open('val.txt', 'w') as f:
    f.write('\n'.join(val) + '\n')
with open('test.txt', 'w') as f:
    f.write('\n'.join(test) + '\n')

print(f"Filtered images: {len(filtered_images)}")
print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

os.system("""grep -v "^image_" ../pasadena_data_256_RGB_train_original/test.txt >> ./test.txt""")
os.system("""grep -v "^image_" ../pasadena_data_256_RGB_train_original/train.txt >> ./train.txt""")
os.system("""grep -v "^image_" ../pasadena_data_256_RGB_train_original/val.txt >> ./val.txt""")