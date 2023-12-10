

def split_list(lst, num_sublists):
    if num_sublists > len(lst):
        num_sublists = len(lst)
    quotient = len(lst) // num_sublists

    remainder = len(lst) % num_sublists

    sublists = []

    start = 0
    for i in range(num_sublists):
        sublist_length = quotient
        if remainder > 0:
            sublist_length += 1
            remainder -= 1

        sublist = lst[start:start + sublist_length]
        sublists.append(sublist)

        start += sublist_length

    return sublists

