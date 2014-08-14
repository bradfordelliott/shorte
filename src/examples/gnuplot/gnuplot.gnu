set terminal pngcairo transparent font "arial,10" linewidth 1 rounded fontscale 1.0 size 500,500
set output "$OUTPUT_FILE"

set title "Temperature Monitor on slice 2" font "Arial Bold,12" textcolor rgb '#A0A0A0'
set yrange [-70:62]
set xrange [0:341]
set ylabel "FINAL[n] Value"
set xlabel "Approximate time in ms"

set style line 1 lc rgb '#8b1a0e' pt 1 ps 1 lt 1 lw 1.5
set style line 2 lc rgb '#5e9c36' pt 6 ps 1 lt 1 lw 1.5

# Set the border style
set style line 11 lc rgb '#808080' lt 1 lw 1.5
set border 3 back ls 11
# Don't show the tics on the right or top of the graph
set tics nomirror

# Add a grid
set style line 12 lc rgb '#C0C0C0' lt 0 lw 2
set grid back ls 12

set tmargin 3
set lmargin 8
set rmargin 1
set bmargin 4

#plot "$DATA_FILE" using 1:2 smooth cspline title "Temperature" with lines ls 1
plot "$DATA_FILE" using 1:2 smooth cspline title "Temperature" with points ls 1
#plot "$DATA_FILE" using 1:2 title "Temperature" with lines ls 1
