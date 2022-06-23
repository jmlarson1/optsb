Gym environment(s) for optsb. Start with general (gym_optsb) and then build custom offline, online, specific parts of the accelerator envs from this.

### TODO
 - [X] clean up action space with discrete values
    - Changed to 6 values only, u/d for 3 quads and believe it is consistent throughout
 - [ ] normalize all state / obs data to 0, 1 -> then adjust state Box space
 - [ ] separate file to choose state input variables
 - [ ] more choice / flexibility with rewards
 - [ ] always more interesting plots needed [sub plots pref]