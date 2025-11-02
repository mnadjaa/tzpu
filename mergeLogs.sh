cat *.txt > merged.txt
grep -v "SEED\|INTER_ARRIVAL_TIMES\|USERS_NUMBER\|USAGE_TIME\|TIME_BETWEEN_LOGINS" merged.txt > mergedFiltered.txt
sed 's/\[/\"\[/g' mergedFiltered.txt > mergedFiltered2.txt
sed -i 's/\]/\]\"/g' mergedFiltered2.txt
sed -i 's/\ \"/\"/g' mergedFiltered2.txt
sed -i 's/\"SLA4_broke\":\([0-9]*\)\,/\"SLA4_broke\":\1/g' mergedFiltered2.txt

cat *.txt > merged.txt
sed 's/\[/\"\[/g' merged.txt > mergedFiltered2.txt
sed -i 's/\]/\]\"/g' mergedFiltered2.txt
sed -i 's/\ \"/\"/g' mergedFiltered2.txt
sed -i 's/\"SLA4_broke\":\([0-9]*\)\,/\"SLA4_broke\":\1/g' mergedFiltered2.txt