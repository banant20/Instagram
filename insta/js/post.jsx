import React from "react";
import PropTypes from "prop-types";
import Comment from "./comment";
class Post extends React.Component {
  /* Display image and post owner of a single post
   */
  
  constructor(props) {
    // Initialize mutable state
    
    super(props);
    this.state = { value: "",imgUrl: "", owner: "", ownerUrl: "", created: "", comments: [], likes: {}, postID: "", input: "", likeid: "", likeUrl: ""};
    //this.toggleLikeButton = this.toggleLikeButton.bind(this);
     this.handleChange = this.handleChange.bind(this);
     this.postComment = this.postComment.bind(this);
     this.changeComment = this.changeComment.bind(this);

    
    
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const postLognameLikesThis = data.likes.lognameLikesThis
        const postNumLikes = data.likes.numLikes
        const likesUrl = data.likes.url
        const input_url = "/api/v1/likes/?postid=" + data.postid
        const postLikes = {
          lognameLikesThis: postLognameLikesThis,
          numLikes: postNumLikes,
          url: likesUrl
        }
        
        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          ownerUrl: data.ownerImgUrl,
          created: data.created,
          comments: data.comments, 
          likes: postLikes,
          postID: data.postid,
          input: input_url,
          likeUrl: likesUrl,
        });
      })
      .catch((error) => console.log(error));
  }
  postLike = () => {
    console.log('button like'); 
    console.log('url: ', this.state.likes.url);
    this.setState(prevState => ({
      likes: {
        //lognameLikesThis)

        lognameLikesThis: !prevState.likes.lognameLikesThis,
        numLikes: prevState.likes.numLikes + 1,
      },
      
    }))
    console.log(this.state.input.toString());
    console.log(this.state.likeUrl); 
    fetch(this.state.input.toString(), {method: ['POST']})
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            this.setState(({likeUrl: data.url}));
            
            console.log(this.state.likeUrl);


    })
    .catch((error) => console.log(error));
    
   
    ;
  }

  
  deleteLike = () => {
      console.log('delete');
      console.log('url: ', this.state.likes.url);
      
    this.setState(prevState => ({
      likes: {
        lognameLikesThis: !prevState.likes.lognameLikesThis,
        numLikes: prevState.likes.numLikes - 1,
        url: null

      }
    }))
    
    fetch(this.state.likeUrl, {method: ["DELETE"]})
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
        })
        // .then((data) => {
        //     console.log(data.likeid);

        // })
        .catch((error) => console.log(error));
    
    ;
 
  }



//   postComment = () => {
//       console.log('post comment'); 

//       this.setState(prevState => ({
//         comments: {
          
//         }
//       }))
//   }
changeComment(input_id) {
  console.log("IN CHANGE COMMENT");
  console.log('the input: ', input_id);
  // console.log('comments before: ', this.state.comments);
  
    this.setState(prevState => ({
        comments:prevState.comments.filter(comment => input_id != comment.commentid),
    }));      
}

handleChange(e) {
  this.setState({value: e.target.value});

}

postComment(e) {
    
    console.log("POSTTT");
    console.log(this.state.value)
    
    //console.log(e.target.value)
    // if (e.key == "Enter") {
    //     console.log("MADE IT");
    // }
    e.preventDefault();
    //submit
    // call api to put in database
    //re render
    //call again 
    const txt = {text:this.state.value}
    console.log(txt);
    this.setState({value: ''});
    const post_c_url = ('/api/v1/comments/?postid=' + (this.state.postID))
    fetch(post_c_url, {method:'POST', headers: {'Content-Type':'application/json; charset=UTF-8'}, body: JSON.stringify(txt),})
    .then((response) => {
        console.log(response);
        if (!response.ok) throw Error(response.statusText);
        return response.json();
    })
    .then((data) => {
        console.log(data);
        // this.setState(prevState => ({
        //   comments: prevState.comments.concat(da),
        // }));
        this.setState(({comments: this.state.comments.concat(data)}));
        

    console.log("printing comments");
    console.log(this.state.comments);

})
.catch((error) => console.log(error));



    // this.setState(prevState => ({
    //     comments: prevState.comments.concat(val),
    // }))
    
}
    

    handleClick =e => {
        console.log(e.detail); 
        switch(e.detail) {
            case 1: {
                console.log('single');
                break; 
            }
            case 2: {
                console.log('double');
                break;
            }
            default: {
                break; 
            }
        }
    };

    
    handleLike = () => {
      console.log('double click');
      console.log('url: ', this.state.likes.url);
      console.log(this.state.likes.lognameLikesThis);
      if (this.state.likes.lognameLikesThis == false) {
        console.log('in');
        this.setState(prevState => (
          {

          likes: {
            //lognameLikesThis)
            lognameLikesThis:true,
            numLikes: prevState.likes.numLikes + 1,
            
          },
          
          
        }))
        console.log('updated', this.state.likes.lognameLikesThis)
        console.log(this.state.input.toString());
        console.log(this.state.likeUrl); 
        fetch(this.state.input.toString(), {method: ['POST']})
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState(({likeUrl: data.url}));
                
                console.log(this.state.likeUrl);

      
                
    
    
        })
        .catch((error) => console.log(error));
        
      }
        
        
       
        ;
      }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl,owner, ownerUrl, created, comments, likes, postID,input, likeUrl, } = this.state;

    // Render post image and post owner
    return (
      
      <div className="post">
        <img src={ownerUrl} alt="profile" />
        <p><a href = {"/posts/" + postID + "/"}>{created}</a></p>
        <p><a href = {"/users/" + owner + "/"}>{owner}</a></p>
        <button><img src={imgUrl} alt="post_image" onDoubleClick={this.handleLike}/></button>
        
         {likes.lognameLikesThis? <button  onClick = {this.deleteLike} className="like-unlike-button">unlike</button> : 
         <button onClick = {this.postLike} className="like-unlike-button">like</button>  }
        {likes.numLikes == 1? <p>{likes.numLikes} like</p> :  <p>{likes.numLikes} likes</p>}
            {comments.map((comment, idx) => {
                return (
                    (<Comment key = {idx} comment = {comment} changeComment = {this.changeComment}/>)
            
                )
            })}

            <form className="comment-form"  onSubmit = {this.postComment}>
            <input type="text" value={this.state.value} onChange = {this.handleChange} />
            </form>

            
       
      </div>
    // index.html
       
    
    );
  }
}
Post.propTypes = {
  url: PropTypes.string.isRequired,
};
export default Post;


