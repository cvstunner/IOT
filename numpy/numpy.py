class numpy():
    def __init__(self):

    def meanListEle(self, arr):
        res = 0
        item = 0
        for i in arr:
            res = res + i
            item += 1

        return res/item

    def sumListEle(arr):
        res = 0
        for i in arr:
            res = res + i

        return res

    def subFromList(arr, data, parity):
        return [parity * (x - data) for x in arr]

    def sum2(data1, data2):
        return data1+data2 

    def shape(self, arr):
        return len(arr)

ir_data = [10, 8, 6, 4, 2]
a = [10, 8, 6, 4, 2]
MA_SIZE = 2

ir_mean = int(np.mean(ir_data))

x = -1 * (np.array(ir_data) - ir_mean)
a = [-(x - ir_mean) for x in a]
print(x)
print(x.shape[0])
print(a)
print(len(a))

for i in range(x.shape[0] - MA_SIZE):
    x[i] = np.sum(x[i : i + MA_SIZE]) / MA_SIZE
print(x)

for i in range(len(a) - MA_SIZE):
    a[i] = (a[i] + a[i + 1]) / MA_SIZE
print(a)
