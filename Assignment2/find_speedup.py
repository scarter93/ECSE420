import sys
def S(n, P, t):
    return (t/(t*(1-P) + P*t/n + 10*n))


runtimes = [300000000, 150000000]
max_f = [0,0]
file = open("speedup_out.txt", 'w')
for i in range(len(runtimes)):
    for n in range(1, 100000):
        max = S(n, .999, runtimes[i])
        if max > max_f[i]:
            max_f[i] = max

print("for runtimes %f" %runtimes[0], end= ", ",file=file)
print("%f" %runtimes[1], end= " ",file=file)
print("the speedups are %f" %max_f[0], end= ", ",file=file)
print("%f" %max_f[1], end= " ",file=file)

file.close()