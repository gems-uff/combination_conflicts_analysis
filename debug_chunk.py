from inspect_util import Chunk
from partial_order import  violates_partial_order

chunk_id = 780839
chunk = Chunk(chunk_id)
print(violates_partial_order(chunk.v1, chunk.v2, chunk.before_context, chunk.after_context, chunk.resolution, chunk_id, True))

