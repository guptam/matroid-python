import os
import requests

from matroid import error
from matroid.src.helpers import api_call, batch_file_request

# https://staging.dev.matroid.com/docs/api/index.html#api-Images-Classify
@api_call(error.InvalidQueryError)
def classify_image(self, detector_id, file=None, url=None, **options):
  """
  Classify an image with a detector

  detector_id: a unique id for the detector
  file: path to local image file to classify
  url: internet URL for the image to classify
  """

  (endpoint, method) = self.endpoints['classify_image']

  if not url and not file:
    raise error.InvalidQueryError(
        message='Missing required parameter: file or url')

  endpoint = endpoint.replace(':key', detector_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {'detector_id': detector_id}
    data.update(options)

    if url:
      if isinstance(url, list):
        data['urls'] = url
      else:
        data['url'] = url
    if file:
      if not isinstance(file, list):
        file = [file]

      return batch_file_request(file, method, endpoint, headers, data)
    else:
      return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except IOError as e:
    raise e
  except error.InvalidQueryError as e:
    raise e
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Images-PostLocalize
@api_call(error.InvalidQueryError)
def localize_image(self, localizer, localizer_label, **options):
  """
  Note: this API is very similar to Images/Classify;
  however, it can be used to update bounding boxes of existing training images
  by supplying update=true, labelId, and one of imageId or imageIds, and it has
  access to the internal face localizer
  (localizer="DEFAULT_FACE" and localizerLabel="face").
  """
  (endpoint, method) = self.endpoints['localize_image']

  data = {
      'localizer': localizer,
      'localizerLabel': localizer_label,
  }

  update = options.get('update')

  if update:
    image_id = options.get('image_id')
    image_ids = options.get('image_ids')

    if not image_id and not image_ids:
      raise error.InvalidQueryError(
          message='Missing required parameter for update: image_id or image_ids')

    if image_id:
      data['imageId'] = image_id
    else:
      data['imageIds'] = image_ids
  else:
    files = options.get('file')
    urls = options.get('url')

    if not files and not urls:
      raise error.InvalidQueryError(
          message='Missing required parameter: files or urls')

    data.update({'files': files,
                 'urls': urls, })

  try:
    headers = {'Authorization': self.token.authorization_header()}

    data.update({'confidence': options.get('confidence'),
                 'update': 'true' if update else '',
                 'maxFaces': options.get('max_faces'),
                 'confidence': options.get('confidence'),
                 'labelId': options.get('label_id')
                 })

    if update:
      return requests.request(method, endpoint, **{'headers': headers, 'data': data})

    if files:
      if not isinstance(files, list):
        files = [files]
      return batch_file_request(files, method, endpoint, headers, data)
    else:
      if isinstance(urls, list):
        data['urls'] = urls
      else:
        data['url'] = urls
      return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except IOError as e:
    raise e
  except error.InvalidQueryError as e:
    raise e
  except Exception as e:
    raise error.APIConnectionError(message=e)
