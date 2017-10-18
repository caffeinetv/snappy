# This file has the crazy import stuff needed to support dependencies inside
# the AWS Lambda runtime.

import os
import sys


here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here))
