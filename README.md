```python
from pyrequire import require

my_package = require("file:///../my_package")
online_package = require("raw.githubusercontent.com/.../online_package.py")

online_package.do_something()   
```