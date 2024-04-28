# SPDX-FileCopyrightText: 2024-present Filippo Vicentini <filippovicentini@gmail.com>
#
# SPDX-License-Identifier: MIT

# set the local path
import os

os.environ["NQX_INTERNAL_ROOT"] = os.path.dirname(__file__) + "/.."
os.environ["NQX_INTERNAL_CONFIG"] = os.path.dirname(__file__) + "/../etc"
del os
