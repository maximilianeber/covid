# REPO for Corona-related Modelling

This is **work in progress**. Please do not quote or re-use.

## Modelling Approach
![Image of Flow](flow.png)

$ \Delta S_t / \Delta t = - \beta(Asympt_t + Incub\_Infect_t + Mild_t ) S_t $

$\Delta Incub\_Non\_Infect_t / \Delta t = \beta(Asympt_t + Incub\_Infect_t + Inf\_Mild_t ) S_t - 1/D\_incubation \cdot Incub\_Non\_Infect_t $

$\Delta Incub\_Infect_t / \Delta t = 1/D\_incubation \cdot Incub\_Non\_Infect_t - 1/D\_presmympt \cdot Incub\_Infect_t  $

$\Delta Asympt_t / \Delta t = 1/D\_presmympt \cdot p\_asympt \cdot Incub\_Infect_t - 1/D\_recovery\_asympt \cdot Asympt_t $

$\Delta Mild_t/ \Delta t = 1/D\_presmympt \cdot p\_mild \cdot Incub\_Infect_t - D\_recovery\_mild \cdot Mild_t $

$\Delta Severe_t / \Delta t = 1/D\_presmympt \cdot p\_severe \cdot Incub\_Infect_t - 1/D\_hospital \cdot Severe_t $

$\Delta Fatal_t / \Delta t = 1/D\_presmympt \cdot p\_fatal \cdot Incub\_Infect_t - 1/D\_hospital \cdot Fatal_t $

$\Delta Severe\_Hosp_t / \Delta t = 1/D\_hospital \cdot Severe_t  - 1/D\_recovery\_severe \cdot Severe\_Hosp_t $

$\Delta Fatal\_Hosp_t / \Delta t = 1/D\_hospital \cdot Fatal_t - 1/D\_death \cdot Fatal\_Hosp_t  $

$\Delta R\_Asympt / \Delta t = 1/D\_recovery\_asympt \cdot Asympt_t $

$\Delta R\_Mild / \Delta t = 1/D\_recovery\_mild \cdot Mild_t $

$\Delta R\_Severe / \Delta t = 1/D\_recovery\_severe \cdot Severe\_Hosp_t $

$\Delta R\_Fatal / \Delta t = 1/D\_death \cdot Fatal\_Hosp_t $


## Related material
* [COVID Calculator](http://gabgoh.github.io/COVID/) ([Code](https://github.com/gabgoh/epcalc/blob/master/src/App.svelte))
* [Jim Stock on liftoff and the importance of the asymptomatic rate](https://drive.google.com/file/d/12MV466ZZy5xHir4xdPhoTrL1oO8CbZU-/view)
