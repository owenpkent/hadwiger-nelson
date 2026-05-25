import Lake
open Lake DSL

package HadwigerNelson where
  -- Package configuration for the Hadwiger-Nelson formalization.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.13.0"

@[default_target]
lean_lib HadwigerNelson where
  -- Library configuration
