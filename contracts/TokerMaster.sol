// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract TokenMaster is ERC721 {
    address public owner;
    uint256 public totalOccasions;
    uint256 public totalSupply;
    using SafeMath for uint256;

    struct Occasion {
        uint256 id;
        string name;
        uint256 cost;
        uint256 tickets;
        uint256 maxTickets;
        string date;
        string time;
        string location;
        uint256 seatsBooked;
        address[] ownershipHistory;
    }

    mapping(uint256 => Occasion) occasions;
    mapping(uint256 => mapping(address => bool)) public hasBought;
    mapping(uint256 => mapping(uint256 => address)) public seatTaken;
    mapping(uint256 => uint256[]) seatsTaken;
    mapping(address => uint) public ticketsPurchased;
    event TransactionSent(address indexed sender, uint256 amount);
    event LogSeatTaken(uint256 occasionId, uint256 seatNumber, address buyer);

    event TicketPurchased(
        uint256 occasionId,
        uint256 seatNumber,
        uint256 ticketCost,
        address buyer
    );
    event TicketRefunded(
        uint256 occasionId,
        uint256 seatNumber,
        uint256 refundAmount,
        address buyer
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol
    ) ERC721(_name, _symbol) {
        owner = msg.sender;
    }

    function list(
        string memory _name,
        uint256 _cost,
        uint256 _maxTickets,
        string memory _date,
        string memory _time,
        string memory _location
    ) public onlyOwner {
        totalOccasions++;
        occasions[totalOccasions] = Occasion(
            totalOccasions,
            _name,
            _cost,
            _maxTickets,
            _maxTickets,
            _date,
            _time,
            _location,
            0,
            new address[](0)
        );
    }

    function bookTicket(uint256 _id, uint256 _seat) public payable {
        Occasion storage occasion = occasions[_id];
        require(occasion.id != 0, "Invalid occasion ID");
        require(
            _seat > 0 && _seat <= occasion.maxTickets,
            "Invalid seat number"
        );
        require(
            seatTaken[occasion.id][_seat] == address(0),
            "Seat is already taken at this address"
        );
        require(
            occasion.seatsBooked < occasion.maxTickets,
            "All seats are booked"
        );
        uint256 ticketCost = occasion.cost;
        require(msg.value >= ticketCost, "Insufficient funds");

        occasion.tickets = occasion.tickets.add(1);
        occasion.seatsBooked = occasion.seatsBooked.add(1);
        seatTaken[occasion.id][_seat] = msg.sender;
        hasBought[occasion.id][msg.sender] = true;
        seatsTaken[occasion.id].push(_seat);
        payable(owner).transfer(ticketCost);
        totalSupply++;

        _mint(msg.sender, totalSupply);
        occasion.ownershipHistory.push(msg.sender);
        emit LogSeatTaken(occasion.id, _seat, msg.sender);
        emit TicketPurchased(occasion.id, _seat, ticketCost, msg.sender);
    }

    function refundTicket(
        uint256 _occasionId,
        uint256 _seatNumber
    ) external onlyOwner {
        Occasion storage occasion = occasions[_occasionId];

        require(occasion.id != 0, "Invalid occasion ID");

        require(
            _seatNumber > 0 && _seatNumber <= occasion.maxTickets,
            "Invalid seat number"
        );

        address buyer = seatTaken[occasion.id][_seatNumber];
        require(buyer != address(0), "Seat is not taken");

        require(hasBought[occasion.id][buyer], "Buyer has not bought a ticket");

        uint256 refundAmount = occasion.cost;
        (bool success, ) = payable(buyer).call{value: refundAmount}("");
        require(success, "Refund failed");

        occasion.tickets = occasion.tickets.sub(1);
        occasion.seatsBooked = occasion.seatsBooked.sub(1);
        seatTaken[occasion.id][_seatNumber] = address(0);
        hasBought[occasion.id][buyer] = false;

        emit TicketRefunded(occasion.id, _seatNumber, refundAmount, buyer);
    }

    function getSeatInfo(
        uint256 _occasionId,
        uint256 _seatNumber
    ) public view returns (uint256 cost, address buyer) {
        Occasion storage occasion = occasions[_occasionId];

        require(occasion.id != 0, "Invalid occasion ID");
        require(
            _seatNumber > 0 && _seatNumber <= occasion.maxTickets,
            "Invalid seat number"
        );

        cost = occasion.cost;
        buyer = seatTaken[occasion.id][_seatNumber];

        require(buyer != address(0), "Seat is not taken");

        return (cost, buyer);
    }

    function getOccasion(uint256 _id) public view returns (Occasion memory) {
        return occasions[_id];
    }

    function getSeatsTaken(uint256 _id) public view returns (uint256[] memory) {
        return seatsTaken[_id];
    }

    function sendTransaction() external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        emit TransactionSent(msg.sender, msg.value);
    }

    function withdraw() public onlyOwner {
        (bool success, ) = owner.call{value: address(this).balance}("");
        require(success);
    }

    function sayHello() external pure returns (string memory) {
        return "Hello world!!";
    }
}
