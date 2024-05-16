# Kimoji

Service to track jobs on remote machines

```
mkdir db
docker build -t kimoji . && 
docker run -p 8000:8000 -v %cd%\db:/db/ kimoji 
```

![Kimoji from Spirited Away, crunching orders.](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2Fce%2F8e%2F3b%2Fce8e3b955b0b1824dd3a4bbf056021bf.gif&f=1&nofb=1&ipt=01df531d50537b5b3b2e1b23d0e80869b0829fef389efb27129ff2c471fcd31d&ipo=images)