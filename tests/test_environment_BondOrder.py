import numpy as np
import freud
import rowan
import unittest
import util


class TestBondOrder(unittest.TestCase):
    def test_bond_order(self):
        """Test the bond order diagram calculation."""
        (box, positions) = util.make_fcc(4, 4, 4)
        quats = np.array([[1, 0, 0, 0]] * len(positions))

        r_max = 1.5
        num_neighbors = 12
        n_bins_theta = n_bins_phi = 6
        bo = freud.environment.BondOrder(r_max, num_neighbors,
                                         n_bins_theta, n_bins_phi)

        # Test access
        with self.assertRaises(AttributeError):
            bo.box
        with self.assertRaises(AttributeError):
            bo.bond_order

        # Test that there are exactly 12 non-zero bins for a perfect FCC
        # structure.
        bo.compute(box, positions, quats)
        op_value = bo.bond_order.copy()
        self.assertEqual(np.sum(op_value > 0), 12)

        # Test access
        bo.box
        bo.bond_order

        # Test all the basic attributes.
        self.assertEqual(bo.n_bins_theta, n_bins_theta)
        self.assertEqual(bo.n_bins_phi, n_bins_phi)
        self.assertEqual(bo.box, box)
        self.assertTrue(np.allclose(
            bo.theta, (2*np.arange(n_bins_theta)+1)*np.pi/6))
        self.assertTrue(np.allclose(
            bo.phi, (2*np.arange(n_bins_phi)+1)*np.pi/12))

        # Test that reset works.
        bo.reset()
        # Test access
        with self.assertRaises(AttributeError):
            bo.box
        with self.assertRaises(AttributeError):
            bo.bond_order

        test_set = util.make_raw_query_nlist_test_set(
            box, positions, positions, "nearest", r_max, num_neighbors, True)
        for ts in test_set:
            bo.reset()
            # Test that lbod gives identical results when orientations are the
            # same.
            #TODO: Find a way to test a rotated system to ensure that lbod gives  # noqa
            # the desired results.
            bo.accumulate(box, ts[0], quats, mode='lbod', nlist=ts[1])
            self.assertTrue(np.allclose(bo.bond_order, op_value))

            # Test access
            bo.box
            bo.bond_order

            # Test that obcd gives identical results when orientations are the
            # same.
            bo.compute(box, ts[0], quats, mode='obcd', nlist=ts[1])
            self.assertTrue(np.allclose(bo.bond_order, op_value))

            # Test that normal bod looks ordered for randomized orientations.
            np.random.seed(10893)
            random_quats = rowan.random.rand(len(positions))
            bo.compute(box, ts[0], random_quats, nlist=ts[1])
            self.assertTrue(np.allclose(bo.bond_order, op_value))

            # Ensure that obcd looks random for the randomized orientations.
            bo.compute(box, ts[0], random_quats, mode='obcd', nlist=ts[1])
            self.assertTrue(not np.allclose(bo.bond_order, op_value))
            self.assertEqual(np.sum(bo.bond_order > 0), bo.bond_order.size)

            # Test that oocd shows exactly one peak when all orientations
            # are the same.
            bo.reset()
            bo.accumulate(box, ts[0], quats, mode='oocd', nlist=ts[1])
            self.assertEqual(np.sum(bo.bond_order > 0), 1)
            self.assertTrue(bo.bond_order[0, 0] > 0)

            # Test that oocd is highly disordered with random quaternions. In
            # practice, the edge bins may still not get any values, so just
            # check that we get a lot of values.
            bo.compute(box, ts[0], random_quats, mode='oocd', nlist=ts[1])
            self.assertGreater(np.sum(bo.bond_order > 0), 30)

    def test_repr(self):
        bo = freud.environment.BondOrder(1.5, 12, 6, 6)
        self.assertEqual(str(bo), str(eval(repr(bo))))

    def test_points_ne_query_points(self):
        lattice_size = 10
        # big box to ignore periodicity
        box = freud.box.Box.square(lattice_size*5)
        angle = np.pi/30
        query_points, points = util.make_alternating_lattice(
            lattice_size, angle)

        r_max = 1.6

        num_neighbors = 12
        n_bins_theta = 30
        n_bins_phi = 2
        test_set = util.make_raw_query_nlist_test_set(
            box, points, query_points, "nearest", r_max, num_neighbors, False)
        for ts in test_set:
            bod = freud.environment.BondOrder(
                r_max=r_max, num_neighbors=num_neighbors,
                n_bins_theta=n_bins_theta, n_bins_phi=n_bins_phi)

            # orientations are not used in bod mode
            ref_orientations = np.array([[1, 0, 0, 0]]*len(points))
            orientations = np.array([[1, 0, 0, 0]]*len(query_points))

            bod.compute(box, ts[0], ref_orientations,
                        query_points, orientations, nlist=ts[1])

            # we want to make sure that we get 12 nonzero places, so we can
            # test whether we are not considering neighbors between points
            self.assertEqual(np.count_nonzero(bod.bond_order), 12)
            self.assertEqual(len(np.unique(bod.bond_order)), 2)


if __name__ == '__main__':
    unittest.main()
