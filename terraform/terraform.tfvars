#
# A default cluster topology.
#
# Author: David Hurta
#

clusters = [
  {
    name = "cluster"
    nodes = [
      {
        type = "control-plane"
      },
      {
        type = "infra"
      },

      {
        type = "cloud"
      },

      {
        type = "edge"
      },
    ]
  }
]