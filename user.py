from trip import Trip

class User:
    """
    A skeleton class for managing user information.
    """
    
    def __init__(self, name=None, email=None, password=None):
      self.name = name
      self.email = email
      self.password = password
      self.trips = []
    
    def __str__(self):
        return f"User(name='{self.name}', email='{self.email}')"

    def new_trip(self):
        city = input("Enter the city: ")
        state = input("Enter the state: ")
        country = input("Enter the country: ")
        start_date = input("Enter the start date: ")
        end_date = input("Enter the end date: ")
        type = input("Enter the type: ")
        self.add_trip(Trip(city, state, country, start_date, end_date, type)) 


    def add_trip(self, trip):
      self.trips.append(trip)

    def remove_trip(self, trip):
        self.trips.remove(trip)

    def get_trips(self):
        return self.trips

    def get_trip(self, index):
        return self.trips[index]


if __name__ == "__main__":
    user = User("Will Cox", "will@gmail.com", "password")
    user.new_trip()
    user.new_trip()
    user_trips = user.get_trips()
    for trip in user_trips:
        print(trip)