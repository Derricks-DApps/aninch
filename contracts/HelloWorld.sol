// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract Storage {
    string public message;

    constructor(){
        message = "Hello World, let get these bounties$$$";
    }

    function setMessage(string memory _message) public{
        message = _message;
    }

    function sayMessage() view public returns (string memory){
        return message;
    }
    
}
