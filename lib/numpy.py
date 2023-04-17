class numpy:
    def meanListEle(arr):
        print(arr)
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

    def shape(arr):
        return len(arr)
