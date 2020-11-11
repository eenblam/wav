#!/usr/bin/env python3


def unity(*args):
    n = len(args)
    return sum(args) / n


def interp(t, xs, duration, exp=1):
    # I think this gets sloppy on the last block,
    # in the sense that it won't fully interpolate.
    # Could update it to detect that we're in a (short) last block
    # and adjust the block_size used for block_ratio accordingly.
    # It's a trade-off:
    # do you want the *rate* your inputs define, or do you want to ultimately reach your final input?

    # xs should be a list of m items
    # Giving n=m-1 blocks between m indices into the duration, with last at end
    n = len(xs) - 1
    # Float division to divide as evenly as possible
    block_size = float(duration) / n
    # This becomes an index into xs, so need an int
    block = int(t / block_size)
    # using % here since pow() requires an int and we aren't doing crypto
    block_pos = t % block_size
    block_ratio = block_pos / block_size
    weight = block_ratio ** exp
    # Linear (could try others) interpolation between values at each end of block
    x1 = xs[block]
    x2 = xs[block+1]
    return x1 * (1 - weight) + x2 * weight


def interp_pairs(t, xs, duration, exp=1):
    # Just like interp(), but sometimes it's handy to have pairs, e.g. pow(_,x,y)

    # xs should be a list of m pairs
    # Giving n=m-1 blocks between m indices into the duration, with last at end
    n = len(xs) - 1
    # Float division to divide as evenly as possible
    block_size = float(duration) / n
    # This becomes an index into xs, so need an int
    block = int(t / block_size)
    # using % here since pow() requires an int and we aren't doing crypto
    block_pos = t % block_size
    block_ratio = block_pos / block_size
    weight = block_ratio ** exp
    # Linear (could try others) interpolation between values at each end of block
    x1,y1 = xs[block]
    x2,y2 = xs[block+1]
    x3 = x1 * (1 - weight) + x2 * weight
    y3 = y1 * (1 - weight) + y2 * weight
    return x3, y3
