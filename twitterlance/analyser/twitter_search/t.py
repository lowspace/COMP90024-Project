print('abv')

import config 

def test(i, like = None, ):
	like = input('once')
	if like:
		print(like)
	print(i)

if __name__ == '__main__':

    test(123)

    print(config.Geocode.keys())
