Gym environment(s) for optsb. Start with general (gym_optsb) and then build custom offline, online, specific parts of the accelerator envs from this.

### TODO
 - [ ] setup a way to then test the fully trained policy after ...
 - [X] clean up action space with discrete values
    - Changed to 6 values only, u/d for 3 quads and believe it is consistent throughout
 - [?] normalize all state / obs data to 0, 1 -> then adjust state Box space
 - [X] did the above inside the playground not the gym env -- NEEDS TO BE CHECKED
 - [ ] force magnet to 2000 value if above or below, return poor reward...
 - [ ] separate file to choose state input variables
 - [ ] more choice / flexibility with rewards
 - [ ] always more interesting plots needed [sub plots pref]