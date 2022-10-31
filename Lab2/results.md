
Index

| Dataset                      | Name                     | index  |
|------------------------------|--------------------------|--------|
| https://tinyurl.com/4vxdw3pa | buchanj-midwinter-00-t   | input1 |
| https://tinyurl.com/kh9excea | carman-farhorizons-00-t  | input2 |
| https://tinyurl.com/dybs9bnk | colby-champlain-00-t     | input3 |
| https://tinyurl.com/datumz6m | cheyneyp-darkbahama-00-t | input4 |
| https://tinyurl.com/j4j4xdw6 | delamare-bumps-00-t      | input5 |
| https://tinyurl.com/ym8s5fm4 | charlesworth-scene-00-t  | input6 |
| https://tinyurl.com/2h6a75nk | delamare-lucy-00-t       | input7 |
| https://tinyurl.com/vwvram8  | delamare-myfanwy-00-t    | input8 |
| https://tinyurl.com/weh83uyn | delamare-penny-00-t      | input9 |


# Spark Iteration 1

| Metrics | pg4300.txt | input1    | input2    | input3    | input4    | input5    | input6    | input7    | input8    | input9    |
|---------|------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| real    | 0m5.040s   | 0m11.101s | 0m10.811s | 0m10.681s | 0m11.011s | 0m10.810s | 0m10.184s | 0m10.903s | 0m11.055s | 0m10.288s |
| user    | 0m9.908s   | 0m0.152s  | 0m0.170s  | 0m0.171s  | 0m0.183s  | 0m0.161s  | 0m0.166s  | 0m0.159s  | 0m0.169s  | 0m0.158s  |
| sys     | 0m0.450s   | 0m0.018s  | 0m0.040s  | 0m0.039s  | 0m0.022s  | 0m0.037s  | 0m0.044s  | 0m0.038s  | 0m0.052s  | 0m0.048s  |


# Spark Iteration 2

| Metrics | input1    | input2    | input3    | input4    | input5    | input6    | input7    | input8    | input9    |
|---------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| real    | 0m11.012s | 0m10.900s | 0m11.088s | 0m11.052s | 0m10.844s | 0m11.405s | 0m10.492s | 0m10.829s | 0m10.730s |
| user    | 0m0.147s  | 0m0.150s  | 0m0.161s  | 0m0.156s  | 0m0.170s  | 0m0.146s  | 0m0.151s  | 0m0.175s  | 0m0.101s  |
| sys     | 0m0.020s  | 0m0.079s  | 0m0.049s  | 0m0.022s  | 0m0.018s  | 0m0.040s  | 0m0.030s  | 0m0.022s  | 0m0.021s  |


# Spark Iteration 3

| Metrics | input1    | input2    | input3    | input4    | input5    | input6    | input7    | input8    | input9    |
|---------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| real    | 0m10.199s | 0m10.870s | 0m10.802s | 0m10.828s | 0m10.872s | 0m10.911s | 0m10.575s | 0m10.672s | 0m10.862s |
| user    | 0m0.128s  | 0m0.150s  | 0m0.182s  | 0m0.172s  | 0m0.152s  | 0m0.170s  | 0m0.160s  | 0m0.104s  | 0m0.152s  |
| sys     | 0m0.020s  | 0m0.050s  | 0m0.040s  | 0m0.040s  | 0m0.040s  | 0m0.035s  | 0m0.040s  | 0m0.080s  | 0m0.040s  |



# Hadoop Iteration 1

| Metrics | input1   | input2   | input3   | input4   | input5   | input6   | input7   | input8   | input9   |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| real    | 0m4.900s | 0m3.794s | 0m4.827s | 0m4.897s | 0m3.825s | 0m3.850s | 0m3.670s | 0m3.040s | 0m3.818s |
| user    | 0m6.889s | 0m5.044s | 0m7.084s | 0m7.500s | 0m5.798s | 0m6.097s | 0m6.524s | 0m6.300s | 0m6.910s |
| sys     | 0m0.371s | 0m0.320s | 0m0.330s | 0m0.370s | 0m0.392s | 0m0.361s | 0m0.329s | 0m0.371s | 0m0.370s |


# Hadoop Iteration 2

| Metrics | input1   | input2   | input3   | input4   | input5   | input6   | input7   | input8   | input9   |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| real    | 0m4.729s | 0m4.014s | 0m4.820s | 0m4.629s | 0m3.821s | 0m3.830s | 0m3.871s | 0m3.903s | 0m3.752s |
| user    | 0m7.411s | 0m6.200s | 0m7.450s | 0m7.478s | 0m5.973s | 0m6.842s | 0m6.759s | 0m6.551s | 0m6.445s |
| sys     | 0m0.370s | 0m0.370s | 0m0.410s | 0m0.340s | 0m0.441s | 0m0.360s | 0m0.406s | 0m0.324s | 0m0.386s |


# Hadoop Iteration 3

| Metrics | input1   | input2   | input3   | input4   | input5   | input6   | input7   | input8   | input9   |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| real    | 0m4.277s | 0m4.144s | 0m4.723s | 0m4.807s | 0m4.811s | 0m3.750s | 0m3.842s | 0m3.684s | 0m3.789s |
| user    | 0m6.981s | 0m7.870s | 0m7.524s | 0m7.426s | 0m6.798s | 0m6.662s | 0m6.660s | 0m6.718s | 0m6.444s |
| sys     | 0m0.440s | 0m0.289s | 0m0.303s | 0m0.291s | 0m0.430s | 0m0.300s | 0m0.329s | 0m0.394s | 0m0.392s |