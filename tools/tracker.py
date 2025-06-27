from __future__ import print_function

import os
import numpy as np
import glob
import time
import argparse
from munkres import Munkres

np.random.seed(0)

def linear_assignment(cost_matrix):
    m = Munkres()
    indexes = m.compute(cost_matrix.tolist())
    return np.array(indexes)


def iou_batch(bb_test, bb_gt):
  bb_gt = np.expand_dims(bb_gt, 0)
  bb_test = np.expand_dims(bb_test, 1)
  
  xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
  yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
  xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
  yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])
  w = np.maximum(0., xx2 - xx1)
  h = np.maximum(0., yy2 - yy1)
  wh = w * h
  o = wh / ((bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])                                      
    + (bb_gt[..., 2] - bb_gt[..., 0]) * (bb_gt[..., 3] - bb_gt[..., 1]) - wh)                                              
  return(o)  


def convert_bbox_to_z(bbox):
  w = bbox[2] - bbox[0]
  h = bbox[3] - bbox[1]
  x = bbox[0] + w/2.
  y = bbox[1] + h/2.
  s = w * h
  r = w / float(h)
  return np.array([x, y, s, r]).reshape((4, 1))


def convert_x_to_bbox(x,score=None):
  w = np.sqrt(x[2] * x[3])
  h = x[2] / w
  if(score==None):
    return np.array([x[0]-w/2.,x[1]-h/2.,x[0]+w/2.,x[1]+h/2.]).reshape((1,4))
  else:
    return np.array([x[0]-w/2.,x[1]-h/2.,x[0]+w/2.,x[1]+h/2.,score]).reshape((1,5))

class KalmanBoxTracker(object):
  count = 0

  def __init__(self, bbox):
      # State vector [cx, cy, s, r, vx, vy, vs]
      self.x = np.zeros((7, 1))
      self.x[:4] = convert_bbox_to_z(bbox)

      # State covariance matrix
      self.P = np.eye(7) * 10.
      self.P[4:, 4:] *= 1000.  # High uncertainty in initial velocity

      # State transition matrix
      self.F = np.eye(7)
      self.F[0, 4] = 1
      self.F[1, 5] = 1
      self.F[2, 6] = 1

      # Observation matrix
      self.H = np.zeros((4, 7))
      self.H[0, 0] = 1
      self.H[1, 1] = 1
      self.H[2, 2] = 1
      self.H[3, 3] = 1

      # Measurement noise
      self.R = np.eye(4) * 0.5
      self.R[2:, 2:] *= 10.

      # Process noise
      self.Q = np.eye(7) * 0.05
      self.Q[6, 6] *= 0.01
      self.Q[4:, 4:] *= 0.05

      # Tracker variables
      self.time_since_update = 0
      self.id = KalmanBoxTracker.count
      KalmanBoxTracker.count += 1
      self.history = []
      self.hits = 0
      self.hit_streak = 0
      self.age = 0

  def predict(self):
      if (self.x[2] + self.x[6]) <= 0:
          self.x[6] = 0

      # Predict state
      self.x = self.F @ self.x
      self.P = self.F @ self.P @ self.F.T + self.Q

      self.age += 1
      if self.time_since_update > 0:
          self.hit_streak = 0
      self.time_since_update += 1

      self.history.append(convert_x_to_bbox(self.x))
      return self.history[-1]

  def update(self, bbox):
      self.time_since_update = 0
      self.history = []
      self.hits += 1
      self.hit_streak += 1

      z = convert_bbox_to_z(bbox)
      y = z - self.H @ self.x  # innovation
      S = self.H @ self.P @ self.H.T + self.R  # innovation covariance
      K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain

      self.x = self.x + K @ y
      self.P = (np.eye(7) - K @ self.H) @ self.P

  def get_state(self):
      return convert_x_to_bbox(self.x)

def associate_detections_to_trackers(detections,trackers,iou_threshold = 0.3):
  if(len(trackers)==0):
    return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,5),dtype=int)

  iou_matrix = iou_batch(detections, trackers)

  if min(iou_matrix.shape) > 0:
    a = (iou_matrix > iou_threshold).astype(np.int32)
    if a.sum(1).max() == 1 and a.sum(0).max() == 1:
        matched_indices = np.stack(np.where(a), axis=1)
    else:
      matched_indices = linear_assignment(-iou_matrix)
  else:
    matched_indices = np.empty(shape=(0,2))

  unmatched_detections = []
  for d, det in enumerate(detections):
    if(d not in matched_indices[:,0]):
      unmatched_detections.append(d)
  unmatched_trackers = []
  for t, trk in enumerate(trackers):
    if(t not in matched_indices[:,1]):
      unmatched_trackers.append(t)

  matches = []
  for m in matched_indices:
    if(iou_matrix[m[0], m[1]]<iou_threshold):
      unmatched_detections.append(m[0])
      unmatched_trackers.append(m[1])
    else:
      matches.append(m.reshape(1,2))
  if(len(matches)==0):
    matches = np.empty((0,2),dtype=int)
  else:
    matches = np.concatenate(matches,axis=0)

  return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort(object):
  def __init__(self, max_age=1, min_hits=3, iou_threshold=0.3):
    self.max_age = max_age
    self.min_hits = min_hits
    self.iou_threshold = iou_threshold
    self.trackers = []
    self.frame_count = 0

  def update(self, dets=np.empty((0, 5))):
    self.frame_count += 1
    trks = np.zeros((len(self.trackers), 5))
    to_del = []
    ret = []
    for t, trk in enumerate(trks):
      pos = self.trackers[t].predict()[0]
      trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
      if np.any(np.isnan(pos)):
        to_del.append(t)
    trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
    for t in reversed(to_del):
      self.trackers.pop(t)
    matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets,trks, self.iou_threshold)

    for m in matched:
      self.trackers[m[1]].update(dets[m[0], :])

    for i in unmatched_dets:
        trk = KalmanBoxTracker(dets[i,:])
        self.trackers.append(trk)
    i = len(self.trackers)
    for trk in reversed(self.trackers):
        d = trk.get_state()[0]
        if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
          ret.append(np.concatenate((d,[trk.id+1])).reshape(1,-1))
        i -= 1

        if(trk.time_since_update > self.max_age):
          self.trackers.pop(i)
    if(len(ret)>0):
      return np.concatenate(ret)
    return np.empty((0,5))

def parse_args():
    parser = argparse.ArgumentParser(description='SORT demo')
    parser.add_argument('--display', dest='display', help='Display online tracker output (slow) [False]',action='store_true')
    parser.add_argument("--seq_path", help="Path to detections.", type=str, default='data')
    parser.add_argument("--phase", help="Subdirectory in seq_path.", type=str, default='train')
    parser.add_argument("--max_age", 
                        help="Maximum number of frames to keep alive a track without associated detections.", 
                        type=int, default=1)
    parser.add_argument("--min_hits", 
                        help="Minimum number of associated detections before track is initialised.", 
                        type=int, default=3)
    parser.add_argument("--iou_threshold", help="Minimum IOU for match.", type=float, default=0.3)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
  args = parse_args()
  display = args.display
  phase = args.phase
  total_time = 0.0
  total_frames = 0
  colours = np.random.rand(32, 3)
  if(display):
    if not os.path.exists('mot_benchmark'):
      print('\n\tERROR: mot_benchmark link not found!\n\n    Create a symbolic link to the MOT benchmark\n    (https://motchallenge.net/data/2D_MOT_2015/#download). E.g.:\n\n    $ ln -s /path/to/MOT2015_challenge/2DMOT2015 mot_benchmark\n\n')
      exit()
    # plt.ion()
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, aspect='equal')

  if not os.path.exists('output'):
    os.makedirs('output')
  pattern = os.path.join(args.seq_path, phase, '*', 'det', 'det.txt')
  for seq_dets_fn in glob.glob(pattern):
    mot_tracker = Sort(max_age=args.max_age, 
                       min_hits=args.min_hits,
                       iou_threshold=args.iou_threshold)
    seq_dets = np.loadtxt(seq_dets_fn, delimiter=',')
    seq = seq_dets_fn[pattern.find('*'):].split(os.path.sep)[0]
    
    with open(os.path.join('output', '%s.txt'%(seq)),'w') as out_file:
      print("Processing %s."%(seq))
      for frame in range(int(seq_dets[:,0].max())):
        frame += 1
        dets = seq_dets[seq_dets[:, 0]==frame, 2:7]
        dets[:, 2:4] += dets[:, 0:2]
        total_frames += 1

        # if(display):
        #   pass
        #   # fn = os.path.join('mot_benchmark', phase, seq, 'img1', '%06d.jpg'%(frame))
        #   # im =io.imread(fn)
        #   # ax1.imshow(im)
        #   # plt.title(seq + ' Tracked Targets')

        start_time = time.time()
        trackers = mot_tracker.update(dets)
        cycle_time = time.time() - start_time
        total_time += cycle_time

        for d in trackers:
          print('%d,%d,%.2f,%.2f,%.2f,%.2f,1,-1,-1,-1'%(frame,d[4],d[0],d[1],d[2]-d[0],d[3]-d[1]),file=out_file)
          # if(display):
          #   d = d.astype(np.int32)
          #   ax1.add_patch(patches.Rectangle((d[0],d[1]),d[2]-d[0],d[3]-d[1],fill=False,lw=3,ec=colours[d[4]%32,:]))

        # if(display):
        #   pass
        #   # fig.canvas.flush_events()
        #   # plt.draw()
        #   # ax1.cla()

  print("Total Tracking took: %.3f seconds for %d frames or %.1f FPS" % (total_time, total_frames, total_frames / total_time))

  if(display):
    print("Note: to get real runtime results run without the option: --display")
