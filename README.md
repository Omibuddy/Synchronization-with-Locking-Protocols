# Synchronization-with-Locking-Protocols

# Transaction Isolation Level Testing Analysis

Based on the output from your transaction isolation level tests, I can provide an analysis of what's happening with each schedule under different isolation levels:

## READ COMMITTED (Default)

### Schedule S1: `r1(x) w2(x) c2 w1(x) r1(x) c1`

- T1 reads the initial value (Item A, 100)
- T2 updates the value to "Updated by T2" and commits
- T1 updates the value to "Updated by T1"
- T1 reads its own update ("Updated by T1", 100)
- T1 commits

This demonstrates the "lost update" phenomenon. T1's update overwrites T2's update without T1 being aware of T2's changes.

### Schedule S2: `r1(x) w2(x) c2 r1(x) c1`

- T1 reads the initial value (Item A, 100)
- T2 updates the value to "Updated by T2" and commits
- T1 reads the updated value from T2 ("Updated by T2", 100)
- T1 commits

This demonstrates that READ COMMITTED allows non-repeatable reads - T1 sees different values for the same query within the same transaction.

### Schedule S3: `r2(x) w1(x) w1(y) c1 r2(y) w2(x) w2(y) c2`

- T2 reads the initial value (Item A, 100)
- T1 updates X and Y values and commits
- T2 reads the updated Y value from T1
- T2 updates X and Y values
- T2 commits

This shows that READ COMMITTED allows a transaction to see committed changes from other transactions.

## REPEATABLE READ

### Schedule S1:

- T1 reads the initial value (Item A, 100)
- T2 writes "Updated by T2" and commits
- Transaction rollback occurs with error: "could not serialize access due to concurrent update"

This demonstrates that REPEATABLE READ prevents the lost update problem by detecting the conflict and forcing a rollback when T1 tries to update data that was modified by T2 after T1 read it.

## SERIALIZABLE

### Schedule S1:

- T1 reads "Updated by T2, 100"

The test was interrupted here, but SERIALIZABLE would provide the strongest isolation guarantees, preventing all anomalies including phantom reads.

## Next Steps for Testing

To complete your testing:

1. **For SERIALIZABLE isolation level**:

   - Continue testing all three schedules to observe how SERIALIZABLE handles conflicts
   - Expect more transaction rollbacks as SERIALIZABLE enforces strict serializability

2. **For SS2PL (Strong Strict Two-Phase Locking)**:

   - Implement explicit locking using `SELECT ... FOR SHARE` and `SELECT ... FOR UPDATE`
   - Compare the results with the database's built-in isolation levels
   - Observe how explicit locking affects transaction behavior

3. **Document observations**:

   - Note which anomalies (lost updates, non-repeatable reads, phantom reads) are prevented at each isolation level
   - Compare the performance implications (rollbacks, deadlocks) of higher isolation levels

4. **Test edge cases**:
   - Try more complex schedules with multiple reads and writes
   - Test with multiple rows to observe range-based anomalies

The output shows PostgreSQL's implementation of isolation levels is working as expected, with higher isolation levels preventing more anomalies but increasing the likelihood of transaction rollbacks.
