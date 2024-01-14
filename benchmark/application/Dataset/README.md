# SGP-Chat

### Questions added to the Dataset so far:

Questions about overall - community
Pprod = power from PV
```
----------
Question1: What would be the profit if the community imports are smaller than this amount of power [10,30,20] from the grid?
Answer Code:
```python
model.st(Pimp<=np.array([10,30,20]))
```
----------
Question2: What would be the profit if the community exports are smaller than this amount of power [10,30,20] to the grid?
Answer Code:
```python
model.st(Pexp<=np.array([10,30,20]))
```
----------
Question3: At the timestep 2 if the community's load doubles, what would be the profit?
Answer Code:
```python
for load in range(Pcons[2]):
	Pcons[2][load] = 2*Pcons[2][load]
```
----------
Question4: What should be the state of energy of the battery if the community's load consumption is reduced to half?
Answer Code:
```python
Pcons = Pcons/2
```
----------
Question5: If the community's load triples, how much I get profit?
Answer Code:
```python
Pcons = Pcons*3
```
----------
Question6: What should be the community's minimum load to get a cost = 0?
Answer Code:
```python
model.st((PriceImp*Pimp).sum() - (PriceEx * Pexp).sum() == 0)
```
----------
Question7: If in the timestep 3 my solar panel generates this amount of power, how much I can take or inject into the grid?
Answer Code:
```python

```
----------
Question8: If my incentive model is flat for all time, how much profit I will have?
Answer Code:
```python

```
----------
Question9: If my incentive model is based on timing, how much profit I will get?
Answer Code:
```python

```
----------
Question10: Why does my battery discharge and charge have this limit?
Answer Code:
```python

```
----------



