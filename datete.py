from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


print(date.today())

print(date.today() - relativedelta(years=3))
