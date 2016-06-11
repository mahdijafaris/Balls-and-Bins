from multiprocessing import Pool


def square(x):
    return x*x


#if __name__ == '__main__':
pool = Pool(processes=4)

result = []
for i in range(10):
    result.append(pool.apply_async(square, (i,)))


print(result[1].get())
