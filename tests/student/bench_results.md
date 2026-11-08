python 3.13.17 | Linux-6.18.44-fc-v310-x86_64-with-glibc2.39 | x86_64
seed=4242 runs=5 warm-up=1 timer=perf_counter unit=milliseconds
|Case|n|m|Seed/generator|Algorithm|Run 1|Run 2|Run 3|Run 4|Run 5|Median|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|
|random|500|50|random.Random(4242+500) random|naive|0.056|0.056|0.044|0.060|0.042|0.056|yes, 1 starts, equal across 3|
|random|500|50|random.Random(4242+500) random|kmp|0.042|0.039|0.062|0.044|0.038|0.042|yes, 1 starts, equal across 3|
|random|500|50|random.Random(4242+500) random|rk|0.072|0.070|0.068|0.068|0.072|0.070|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|naive|0.135|0.130|0.137|0.130|0.131|0.131|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|kmp|0.152|0.118|0.115|0.119|0.115|0.118|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|rk|0.249|0.211|0.213|0.209|0.225|0.213|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|naive|0.274|0.362|0.329|0.268|0.283|0.283|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|kmp|0.271|0.263|0.245|0.261|0.239|0.261|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|rk|0.481|0.429|0.433|0.456|0.425|0.433|yes, 1 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|naive|1.059|1.357|1.240|1.059|1.032|1.059|yes, 0 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|kmp|0.060|0.068|0.058|0.097|0.058|0.060|yes, 0 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|rk|0.071|0.071|0.073|0.073|0.071|0.071|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|naive|9.660|9.957|9.517|10.815|9.863|9.863|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|kmp|0.177|0.182|0.192|0.182|0.181|0.182|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|rk|0.231|0.234|0.221|0.220|0.218|0.221|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|naive|50.497|40.273|41.212|43.797|42.621|42.621|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|kmp|0.976|0.413|0.379|0.442|0.378|0.413|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|rk|0.471|0.479|2.009|0.479|0.498|0.479|yes, 0 starts, equal across 3|
