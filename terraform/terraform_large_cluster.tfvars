#
# A large cluster topology.
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
        type = "infra"
      },
      {
        type = "cloud"
      },
      {
        type = "cloud"
      },
      {
        type = "edge"
      },
      {
        type = "edge"
      },
    ]
  }
]
