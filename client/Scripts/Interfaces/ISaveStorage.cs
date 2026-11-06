using System;
using MergeKingdom.SaveSystem.Models;

namespace MergeKingdom.SaveSystem.Interfaces
{
    /// <summary>
    /// Interface Segregation Principle (ISP):
    /// Segregated contract for local persistence. High-level modules do not need to know whether
    /// storage is encrypted, in PlayerPrefs, or in atomic local files.
    /// </summary>
    public interface ISaveStorage
    {
        SaveDataV2 Load();
        void Save(SaveDataV2 data);
        bool Exists();
        void Clear();
    }

    /// <summary>
    /// Liskov Substitution Principle (LSP):
    /// Encapsulates conflict resolution strategy. Any strategy must satisfy the invariant:
    /// "No player may lose progress, or anything that they paid for."
    /// </summary>
    public interface IConflictResolver
    {
        SaveDataV2 Resolve(SaveDataV2 local, SaveDataV2 incoming);
    }

    /// <summary>
    /// Contract for communicating with the game cloud backend.
    /// </summary>
    public interface ICloudSyncClient
    {
        void Upload(SaveDataV2 data, Action<SaveDataV2> onSuccess, Action<string> onFailure);
        void FetchLatest(string playerId, Action<SaveDataV2> onSuccess, Action<string> onFailure);
    }

    /// <summary>
    /// Abstraction for time to decouple logic from untrusted local system clocks.
    /// Dependency Inversion Principle (DIP): Allows injecting server-synchronized monotonic time.
    /// </summary>
    public interface ITimeProvider
    {
        long GetCurrentUnixTimeSeconds();
    }
}

