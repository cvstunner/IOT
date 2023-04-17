arr = [10.1, 8, 6, 4, 2]


def sum(arr):
    res = 0
    for i in arr:
        res = res + i

    return res


def mean(arr):
    res = 0
    item = 0
    for i in arr:
        res = res + i
        item += 1

    return res / item


def sub(arr, data, parity):
    return [parity * (x - data) for x in arr]


def sum(data1, data2):
    return data1 + data2


print(int(mean(arr)))
