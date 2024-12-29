# this test is meaningful only, when the firmware supports complex arrays

try:
    from ulab import numpy as np
except:
    import numpy as np

dtypes = (np.uint8, np.int8, np.uint16, np.int16, np.float, np.complex)

for dtype in dtypes:
    a = np.array(range(4), dtype=dtype)
    b = a.reshape((2, 2))
    print('\narray:\n', a)
    print('\nexponential:\n', np.exp(a))
    print('\narray:\n', b)
    print('\nexponential:\n', np.exp(b))


a = np.array([0, 1j, 2+2j, 3-3j], dtype=np.complex)
b = np.array([0, 1j, 2+2j, 3-3j] * 2, dtype=np.complex).reshape((2, 4))
c = np.array([0, 1j, 2+2j, 3-3j] * 2, dtype=np.complex).reshape((2, 2, 2))
d = np.array([0, 1j, 2+2j, 3-3j] * 4, dtype=np.complex).reshape((2, 2, 2, 2))

for m in (a, b, c, d):
    print('\n\narray:\n', m)
    print('\nexponential:\n', np.exp(m))
