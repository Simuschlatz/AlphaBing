# from time import sleep
# from random import random
# import multiprocessing
# from contextlib import contextmanager
# import os, sys

# import multiprocessing as mp
# import tensorflow as tf

# def predict_and_sort(model_graph, input_data, output_queue):

#     # Load the model graph
#     tf.import_graph_def(model_graph)

#     # Get the input and output tensors
#     inputs = g.get_tensor_by_name('input:0')
#     outputs = g.get_tensor_by_name('output:0')

#     # Make the prediction
#     predictions = sess.run(outputs, feed_dict={inputs: input_data})

#     # Sort the output and add it to the queue
#     sorted_output = sorted(predictions[0], reverse=True)
#     output_queue.put(sorted_output)

# def parallel_predict_and_sort(model, input_data, num_processes):
#     # Create a queue to hold the results
#     output_queue = mp.Queue()

#     # Split the input data into chunks for each process
#     chunk_size = len(input_data) // num_processes
#     chunks = [input_data[i:i+chunk_size] for i in range(0, len(input_data), chunk_size)]

#     # Start the processes
#     processes = []
#     for chunk in chunks:
#         p = mp.Process(target=predict_and_sort, args=(model, chunk, output_queue))
#         p.start()
#         processes.append(p)

#     # Wait for the processes to finish
#     for p in processes:
#         p.join()

#     # Collect the results
#     results = []
#     while not output_queue.empty():
#         results.append(output_queue.get())

#     # Flatten and return the results
#     return [item for sublist in results for item in sublist]


# if __name__ == '__main__':
#     import tensorflow as tf
#     multiprocessing.freeze_support()
#     inputs = tf.range(0, 8)
#     m = tf.keras.Sequential([
#         tf.keras.layers.InputLayer(1, dtype=tf.float32),
#         tf.keras.layers.Dense(100, activation=tf.keras.activations.relu),
#         tf.keras.layers.Dense(100, activation=tf.keras.activations.relu),
#         tf.keras.layers.Dense(1)
#     ])
    
#     res = parallel_predict_and_sort(m, inputs, 8)
#     print(res)


import concurrent.futures
import tensorflow as tf
import multiprocessing

# Define the worker function
def worker(input_data):
    # Load the model
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(1, dtype=tf.float32),
        tf.keras.layers.Dense(100, activation=tf.keras.activations.relu),
        tf.keras.layers.Dense(100, activation=tf.keras.activations.relu),
        tf.keras.layers.Dense(1)
    ])
    # Make a prediction on the input data
    predictions = model.predict(tf.expand_dims(input_data, 0))
    # Sort the output data
    sorted_data = tf.sort(predictions, direction='DESCENDING')
    return sorted_data
if __name__ == '__main__':
    import tensorflow as tf
    multiprocessing.freeze_support()
    # Define some input data
    input_data = tf.range(0, 8)

    # Create a ThreadPoolExecutor with the desired number of workers
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        # Submit the worker function to the executor for each input data
        futures = [executor.submit(worker, data) for data in input_data]
        concurrent.futures.wait(futures)
        # Get the results from the futures as they complete
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Print the sorted output data
    for result in results:
        print(result.numpy())
