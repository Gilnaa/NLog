INCLUDES=-I../include
SOURCES=main.cpp
OBJECTS:=$(SOURCES:.cpp=.o)

.PHONY: all clean

all: nlog

nlog: $(OBJECTS)
	@$(CC) $(OBJECTS) -lstdc++ -o nlog
	@./nlog_scripts/scrub.py nlog nlog.dict

%.o: %.cpp
	@$(CXX) $< $(INCLUDES) -c -DNLOG_OBJECT_ID=$$(./nlog_scripts/gen_id.py main.cpp --type=content)

clean:
	@rm -f main.o nlog nlog.dict