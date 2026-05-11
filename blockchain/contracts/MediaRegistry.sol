// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MediaRegistry {
    struct MediaRecord {
        address creator;
        bytes32 manifestHash;
        uint256 timestamp;
        bool exists;
    }

    mapping(bytes32 => MediaRecord) private records;

    event MediaRegistered(address indexed creator, bytes32 indexed mediaHash, bytes32 manifestHash, uint256 timestamp);

    function registerMedia(bytes32 mediaHash, bytes32 manifestHash) external {
        require(!records[mediaHash].exists, "Already registered");
        records[mediaHash] = MediaRecord(msg.sender, manifestHash, block.timestamp, true);
        emit MediaRegistered(msg.sender, mediaHash, manifestHash, block.timestamp);
    }

    function getMediaRecord(bytes32 mediaHash) external view returns (address, bytes32, uint256, bool) {
        MediaRecord memory r = records[mediaHash];
        return (r.creator, r.manifestHash, r.timestamp, r.exists);
    }
}
