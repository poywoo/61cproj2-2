from pyspark import SparkContext
import Sliding, argparse

def bfs_map(value):
    items = []
    if value[1] < level: 
        items.append((value[0],value[1]))
    if value[1] == level-1:
        children_board = Sliding.hash_to_board(WIDTH, HEIGHT, value[0])
        children = Sliding.children(WIDTH, HEIGHT, children_board)
        for child in children:
            items.append((Sliding.board_to_hash(WIDTH, HEIGHT, child), value[1] + 1))
    return items

def bfs_reduce(value1, value2):
    return min(value1, value2)

def solve_puzzle(master, output, height, width, slaves):
    global HEIGHT, WIDTH, level
    HEIGHT=height
    WIDTH=width
    level = 0

    sc = SparkContext(master, "python")

    """ YOUR CODE HERE """
    sol_board = Sliding.solution(WIDTH, HEIGHT)
    sol = Sliding.board_to_hash(WIDTH, HEIGHT, sol_board)
    all_sols = sc.parallelize([(sol, level)]) #create an RDD 
    before_count = 1
    k = 0 #counter for iterations of partitionBy
    c = 0 #counter for iterations of count()
    while True:
        level += 1
        all_sols = all_sols.flatMap(bfs_map)
        if k%4 == 0: #every 4 iterations, use parititionBy
            all_sols = all_sols.partitionBy(PARTITION_COUNT)
        all_sols = all_sols.reduceByKey(bfs_reduce)
        if c%2 == 0: #every 2 iterations, use count()
            after_count = all_sols.count()
            if before_count == after_count:
                break
            before_count = after_count
        k += 1
        c += 1

    """ YOUR OUTPUT CODE HERE """
    all_sols = all_sols.map(lambda a: (a[1], a[0])).sortByKey()
    all_sols.coalesce(slaves).saveAsTextFile(output)
    sc.stop()



""" DO NOT EDIT PAST THIS LINE

You are welcome to read through the following code, but you
do not need to worry about understanding it.
"""

def main():
    """
    Parses command line arguments and runs the solver appropriately.
    If nothing is passed in, the default values are used.
    """
    parser = argparse.ArgumentParser(
            description="Returns back the entire solution graph.")
    parser.add_argument("-M", "--master", type=str, default="local[8]",
            help="url of the master for this job")
    parser.add_argument("-O", "--output", type=str, default="solution-out",
            help="name of the output file")
    parser.add_argument("-H", "--height", type=int, default=2,
            help="height of the puzzle")
    parser.add_argument("-W", "--width", type=int, default=2,
            help="width of the puzzle")
    parser.add_argument("-S", "--slaves", type=int, default=6,
            help="number of slaves executing the job")
    args = parser.parse_args()

    global PARTITION_COUNT
    PARTITION_COUNT = args.slaves * 16

    # call the puzzle solver
    solve_puzzle(args.master, args.output, args.height, args.width, args.slaves)

# begin execution if we are running this file directly
if __name__ == "__main__":
    main()
