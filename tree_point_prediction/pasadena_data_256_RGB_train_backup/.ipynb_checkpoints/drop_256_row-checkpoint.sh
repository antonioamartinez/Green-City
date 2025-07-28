for f in csv/*.csv; do
  awk -F, '($1 != 256) && ($2 != 256)' "$f" > tmp && mv tmp "$f"
done
