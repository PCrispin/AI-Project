import numpy as np

# So if you were looking for a gaussian distribution around the address of x = 200 and using a standard deviation of 10, that will give 68% within ±10 squares, 95% within ±20 and 97.3% within ±30 squares.

xNew = np.random.normal(128, 10)

# But, you need further is better. So we need to invert it.  This can be done with subtracting the answer from the limit of the range. This will technically no longer be a probability distribution because the area under the graph will no longer be 1.  But it will serve your purpose.

# The maths is easier if we use np.random.normal around x=0, and then move it to mu when we invert it.  I have also capped the range with min/max

mu = 200  # mid point - use x or z from minecraft
sigma = 10  # Standard deviation.
range = sigma * 3  # Result will be within mu ±range
xNew = np.random.normal(0, sigma)  # Get value centered on 0 with gaussian distribution
xNew = (
    range - min(xNew, range) + mu if xNew > 0 else range * -1 - max(xNew, -range) + mu
)  # invert, cap and move to mu

# The caveat is that for the 0.3% of values that were outside of ±(sigma * 3), they will become ±(sigma * 3).  So the distribution will be slightly off.
print("")
