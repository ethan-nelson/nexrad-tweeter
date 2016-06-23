# radar tweeter (still developing)

Creates a loop from the most recent full hour using the Amazon AWS radar warehouse, then tweets out a resulting gif. 

`hourly.py` runs everything. Ensure your Twitter credentials are saved as environmental variables. The radar site also needs to be changed in the `get_filenames()` call if you want something other than KMKX.


