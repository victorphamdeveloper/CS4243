import sys

class PerspectiveProjector:
	##################### CONSTANTS DECLARATION ##########################
	CONST_u_0 = 0
	CONST_v_0 = 0
	CONST_BETA_U = 1
	CONST_BETA_V = 1
	CONST_k_U = 1
	CONST_k_V = 1
	CONST_FOCAL_LENGTH = 1

	CONST_ROTATIONAL_AXIS = np.array([0, 1, 0])

	def __init__(self):
		print "Constructor for class PerspectiveProjector"
		return

	##################### SUPPORT FUNCTIONS ##############################
	# Function for multiplying quaternion
	def qualtmult(p, q):
		p0 = p[0]
		p1 = p[1]
		p2 = p[2]
		p3 = p[3]
		q0 = q[0]
		q1 = q[1]
		q2 = q[2]
		q3 = q[3]

		# Start computing
		out = [0, 0, 0, 0] #output array
		out[0] = p0 * q0 - p1 * q1 - p2 * q2 - p3 * q3
		out[1] = p0 * q1 + p1 * q0 + p2 * q3 - p3 * q2
		out[2] = p0 * q2 - p1 * q3 + p2 * q0 + p3 * q1
		out[3] = p0 * q3 + p1 * q2 - p2 * q1 + p3 * q0

		return out

	# Retrieve corresponding quaternion from angle and rotational axis
	def getQuaternion(rotationalAxis, angle):
		cosAngle = np.cos(angle / 2.0)
		sinAngle = np.sin(angle / 2.0) 
		return np.array([cosAngle, 0, sinAngle, 0])

	# Function to translate the camera 
	def translateCameraWithAngle(cameraPos, rotationalAxis, angle):
		q = getQuaternion(rotationalAxis, angle)
		negate_q = np.array([q[0], -q[1], -q[2], -q[3]])
		cameraQuaternion = np.array([0, cameraPos[0], cameraPos[1], cameraPos[2]])
		result = qualtmult(qualtmult(q, cameraQuaternion), negate_q)
		return np.array([result[1], result[2], result[3]])

	# Function to create rotation matrix from quaternion
	def quat2rot(q) :
		q0 = q[0]
		q1 = q[1]
		q2 = q[2]
		q3 = q[3]

		#Start computing
		out = np.zeros((3, 3))
		out[0][0] = np.power(q0, 2) + np.power(q1, 2) - np.power(q2, 2) - np.power(q3, 2)
		out[0][1] = 2 * (q1 * q2 - q0 * q3)
		out[0][2] = 2 * (q1 * q3 + q0 * q2)
		out[1][0] = 2 * (q1 * q2 + q0 * q3)
		out[1][1] = np.power(q0, 2) + np.power(q2, 2) - np.power(q1, 2) - np.power(q3, 2)
		out[1][2] = 2 * (q2 * q3 - q0 * q1)
		out[2][0] = 2 * (q1 * q3 - q0 * q2)
		out[2][1] = 2 * (q2 * q3 + q0 * q1)
		out[2][2] = np.power(q0, 2) + np.power(q3, 2) - np.power(q1, 2) - np.power(q2, 2)

		return np.matrix(out)

	# Show points in perspective projection view
	def displayInPerspectiveView(initialCameraPos, pts, rotationalAxis, angle):
		xCoords = np.zeros(len(pts))
		yCoords = np.zeros(len(pts))
		cameraRotationalAxes = quat2rot(getQuaternion(rotationalAxis, i * angle))
		cameraPos = translateCameraWithAngle(initialCameraPos, rotationalAxis, - i * angle)

		for j in range(len(pts)):
			point = pts[j, :]
			xCoords[j] = CONST_FOCAL_LENGTH * np.inner(point - cameraPos, cameraRotationalAxes[0, :]) * CONST_BETA_U / (np.inner(point - cameraPos, cameraRotationalAxes[2, :])) + CONST_u_0
			yCoords[j] = CONST_FOCAL_LENGTH * np.inner(point - cameraPos, cameraRotationalAxes[1, :]) * CONST_BETA_V / (np.inner(point - cameraPos, * cameraRotationalAxes[2, :])) + CONST_v_0

		return zip(xCoords, yCoords)
