# from ast import Constant
# from doctest import ELLIPSIS_MARKER
# from operator import truediv


TT_BOOL = 'true'+'false'
# LETTERS = ['a','n','d', 'o', 'r', 't', 'e', 'u', 'f', 'l', 's']

# class Node:
#     def __init__(self, key, value):
#         self.key = key
#         self.value = value
#         self.next = None

# class HashMap:
#     def __init__(self):
#         self.store = [None for _ in range(16)]
#     def get(self, key):
#         index = hash(key) & 15
#         if self.store[index] is None:
#             return None
#         n = self.store[index]
#         while True:
#             if n.key == key:
#                 return n.value
#             else:
#                 if n.next:
#                     n = n.next
#                 else:
#                     return None
#     def put(self, key, value):
#         nd = Node(key, value)
#         index = hash(key) & 15
#         n = self.store[index]
#         if n is None:
#             self.store[index] = nd
#         else:
#             if n.key == key:
#                 n.value = value
#             else:
#                 while n.next:
#                     if n.key == key:
#                         n.value = value
#                         return
#                     else:
#                         n = n.next
#                 n.next = nd

# TT_DD = 12
# hm = HashMap()

# hm.put("tut", TT_DD)
# po = hm.get("tut")


# word = 'true'

# word = word.upper()


# b = 5
# a = 3 if b > 4 else print("s")


# z = True

# x = int('2')

# print(x)

# print(type(z))


# string = "haha"
# print(len(string))
# for char in range(len(string)):
#     print(string[char])
# zahl = 4

# if zahl % 2 == 0:
#     print("gerade")


# bool_list = [True, False]


# print(str(bool_list))

# i = Token(TT_TRUE)

# print(i.type)

# text = "true and false"
# expected_list = ['true', 'and', 'false']
# for i in range(len(expected_list)):
#     expected_list[i] = expected_list[i].upper()s

# luste = [Token(TT_TRUE), Token(TT_AND), Token(TT_FALSE)]
# print(luste[1].type)


TT_TEST = '<'

if '<' == TT_TEST:
    print('sss')
