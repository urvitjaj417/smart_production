CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -std=c99
LIBS    = -lm
TARGET  = sensor_sim
SRC     = sensor_sim.c

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LIBS)
	@echo "Build OK -> ./$(TARGET)"

run: $(TARGET)
	./$(TARGET) 3000 ../data/sensor_data.csv

clean:
	rm -f $(TARGET)
