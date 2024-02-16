from loader import root
from database import models


if __name__ == "__main__":
    models.db.connect()
    root.mainloop()
