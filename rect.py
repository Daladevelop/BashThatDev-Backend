from point import Point
class Rect:
	def __init__(self, x, y, w, h):
		self.x = float(x)
		self.y = float(y)
		self.w = float(w)
		self.h = float(h)

	def min_x(self):
		return self.x

	def min_y(self):
		return self.y

	def max_x(self):
		return self.x + self.w

	def max_y(self):
		return self.y + self.h

	def center(self):
		return Point((self.min_x() + self.max_x()) / 2, (self.min_y() + self.max_y()) / 2)

	def left_center(self):
		return Point(self.min_x(), (self.min_y() + self.max_y()) / 2)

	def right_center(self):
		return Point(self.max_x(), (self.min_y() + self.max_y()) / 2) 

	def top_center(self):
		return Point((self.min_x() + self.max_x()) / 2, self.min_y())

	def bottom_center(self):
		return Point((self.min_x() + self.max_x()) / 2, self.max_y())


